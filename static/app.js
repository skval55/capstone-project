let dailyData;
let userActivity;
$(".search-day").click(getDayAndActivity);
$("#changeLocation").click(changeLocation);
$("#load").ready(getData);

async function getDayAndActivity(e) {
  $(".days").html("");
  const response = await axios.get(`/api/search-activity/${e.target.id}`);
  userActivity = response.data.search.activity;
  const filteredDays = filterDays(userActivity, dailyData);
  for (day in filteredDays) {
    console.log(dailyData[day]);
    makeHtmlCard(day, e);
  }
}

function makeHtmlCard(day, e) {
  const dayData = dailyData[day];
  const myDate = new Date(dayData.dt * 1000);
  let icon = dailyData[day].weather[0].icon;
  let theme = "light";
  let moonDetails;
  const timeOfDay = Object.keys(filteredDays[day][0]).filter(
    (time) => !["min", "max"].includes(time)
  );
  if (filteredDays[day][1] == false) {
    moonDetails = "hidden";
  }
  if (timeOfDay.includes("night")) {
    icon = icon.slice(0, 2) + "n";
    theme = "dark";
  }
  $(`#activity${e.target.id}`)
    .append(`<div> <div class="temps${day}">best time to go ${
    userActivity.name
  } would be in the ${timeOfDay}</div>
    <div class=' ${theme}'><img src="https://openweathermap.org/img/wn/${icon}@2x.png" alt="">
    <h3>${myDate.toLocaleString()}</h3>
    <div>${dailyData[day].weather[0].description}</div>
   <div>High: ${dailyData[day].temp.max} Low: ${dailyData[day].temp.min}</div>
   <div>Morning: ${dailyData[day].temp.morn} Day: ${
    dailyData[day].temp.day
  } Evening: ${dailyData[day].temp.eve} Night: ${
    dailyData[day].temp.night
  }</div>
    <div>Sunrise ${new Date(
      dailyData[day].sunrise * 1000
    ).toLocaleString()}</div>
    <div>Sunset ${new Date(dailyData[day].sunset * 1000).toLocaleString()}</div>
    <div class="${moonDetails} ">
    <div>Moonrise ${new Date(
      dailyData[day].moonrise * 1000
    ).toLocaleString()}</div>
    <div>Moonset ${new Date(
      dailyData[day].moonset * 1000
    ).toLocaleString()}</div>
    <div>Moon coverage ${dailyData[day].moon_phase * 100}%</div>
    </div>
    <div>Percentage of Rain ${dailyData[day].pop * 100}%</div>
    <div>UVI ${dailyData[day].uvi} (highest between 11am - 2pm)</div>
    </div>
    </div>
    `);
}

async function getData() {
  const response = await axios.get(`/api/get-day-data`);
  dailyData = response.data.search.days.daily;
}

async function changeLocation(e) {
  e.preventDefault();
  const city = $("#city").val();
  const state = $("#state").val();
  const response = await axios.get(
    `http://api.openweathermap.org/geo/1.0/direct?q=${city},${state},USA&limit=1&appid=296cd6aaf1d515387c708caa99264128`
  );
  const lat = response.data[0].lat;
  const lon = response.data[0].lon;

  const weatherResponse = await axios.get(
    `https://api.openweathermap.org/data/3.0/onecall?lat=${lat}&lon=${lon}&units=imperial&exclude=hourly,minutely,current&appid=296cd6aaf1d515387c708caa99264128`
  );
  dailyData = weatherResponse.data.daily;
}

function filterDays(activity, days) {
  filteredActivity = filterActivity(activity);
  daysObj = {};
  filteredDays = {};
  for (day in days) {
    const singleDay = {};
    singleDay["temp"] = days[day].temp;
    singleDay["moonPhase"] = days[day].moon_phase;
    singleDay["weatherCondition"] = days[day].weather[0].main;
    singleDay["uvi"] = days[day].uvi;
    daysObj[day] = singleDay;
  }
  for (day in daysObj) {
    if (filteredActivity.weather_condition) {
      filterWeatherCondition();
    }
    if (filteredActivity.uvi) {
      filterUvi();
    }
    if (filteredActivity.moon_phase) {
      filterMoonPhase();
    }

    if (!(daysObj[day] === false)) {
      filterDaylight();

      if (filteredActivity.max_temp) {
        filterMax(daysObj[day]);
      }
      if (filteredActivity.min_temp) {
        filterMin(daysObj[day]);
      }
    }

    if (daysObj[day]["temp"]) {
      if (Object.keys(daysObj[day]["temp"]).length > 0) {
        filteredDays[day] = [daysObj[day]["temp"], filteredActivity.show_moon];
      }
    }
  }
  return filteredDays;
}

function filterActivity(activity) {
  const asArray = Object.entries(activity);
  const filtered = asArray.filter(
    ([key, value]) => ![null, "{}"].includes(value)
  );
  const filteredObj = Object.fromEntries(filtered);
  return filteredObj;
}

function filterMax(tempDay) {
  const asArray = Object.entries(tempDay.temp);
  const filtered = asArray.filter(
    ([key, value]) => value < filteredActivity.max_temp
  );
  const filteredTemps = Object.fromEntries(filtered);
  daysObj[day]["temp"] = filteredTemps;
}

function filterMin(tempDay) {
  const asArray = Object.entries(tempDay.temp);
  const filtered = asArray.filter(
    ([key, value]) => value > filteredActivity.min_temp
  );
  const filteredTemps = Object.fromEntries(filtered);
  daysObj[day]["temp"] = filteredTemps;
}

function filterWeatherCondition() {
  const weather_condition = filteredActivity.weather_condition
    .replace("{", "")
    .replace("}", "")
    .split(",");
  if (!weather_condition.includes(daysObj[day]["weatherCondition"])) {
    daysObj[day] = false;
  }
}
function filterUvi() {
  const uviNums = filteredActivity.uvi.split(",");
  if (
    !(
      daysObj[day]["uvi"] >= parseFloat(uviNums[0]) &&
      daysObj[day]["uvi"] <= parseFloat(uviNums[1])
    )
  ) {
    daysObj[day] = false;
  }
}
function filterMoonPhase() {
  const moonPhaseNums = filteredActivity.moon_phase.split(",");
  if (
    !(
      daysObj[day]["moonPhase"] >= parseFloat(moonPhaseNums[0]) &&
      daysObj[day]["moonPhase"] <= parseFloat(moonPhaseNums[1])
    )
  ) {
    daysObj[day] = false;
  }
}
function filterDaylight() {
  if (filteredActivity.sun == true) {
    const asArray = Object.entries(daysObj[day]["temp"]);
    const filtered = asArray.filter(([key, value]) =>
      ["day", "morn", "eve", "max", "min"].includes(key)
    );
    const filteredTemps = Object.fromEntries(filtered);
    daysObj[day]["temp"] = filteredTemps;
  } else {
    const asArray = Object.entries(daysObj[day]["temp"]);
    const filtered = asArray.filter(([key, value]) => key === "night");
    const filteredTemps = Object.fromEntries(filtered);
    daysObj[day]["temp"] = filteredTemps;
  }
}
