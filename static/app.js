// ***********************************************
// global variables

let dailyData;
let userActivity;
let city = "";
let state = "";

// ***********************************************
// event listeners
$(".search-day").click(getDayAndActivity);
$("#changeLocation").click(changeLocation);
if ($(".load").length > 0) {
  $(".load").ready(getData);
}
//

// **********************************************
// landing page changing text
let counter = 0;
const landingPageTextArray = [
  "Easily plan activities according to the weather",
  "Connect with others to plan and prepare for activities",
];

function fadeInandOut() {
  $("#landing-page-text").fadeOut(500, function () {
    $(this).text(landingPageTextArray[counter]).fadeIn(500);

    if (counter == 1) {
      counter = 0;
    } else {
      counter++;
    }
  });
}

setInterval(fadeInandOut, 3500);

// **********************************************
// Toggle between sign up and sign in form
$(".show-sign-up-form").click(function (e) {
  e.preventDefault();
  $("#sign-in").toggleClass("hidden");
  $("#sign-up").toggleClass("hidden");
  $("#sign-up  span").text("");
  $("#sign-in span").text("");
});

async function changeLocation(e) {
  e.preventDefault();
  $("#flash-container-js").addClass("hidden");
  $("#flash-container-js").text("");
  city = $("#city").val();
  state = $("#state").val();
  try {
    const response = await axios.get(
      `http://api.openweathermap.org/geo/1.0/direct?q=${city},${state},USA&limit=1&appid=296cd6aaf1d515387c708caa99264128`
    );
    const lat = response.data[0].lat;
    const lon = response.data[0].lon;
    const weatherResponse = await axios.get(
      `https://api.openweathermap.org/data/3.0/onecall?lat=${lat}&lon=${lon}&units=imperial&exclude=hourly,minutely,current&appid=296cd6aaf1d515387c708caa99264128`
    );
    dailyData = weatherResponse.data.daily;

    $("#city").val("");
    $("#state").val("");
    $(".city").text(city);
    $(".state").text(state);
    console.log(city);
  } catch (error) {
    $("#flash-container-js").text("City/State not found");
    $("#flash-container-js").toggleClass("hidden");
  }
}

// **********************************************
// gets activity and days and filters the days to put on screen the filtered days
async function getDayAndActivity(e) {
  $(".days").html("");
  const response = await axios.get(`/api/search-activity/${e.target.id}`);
  userActivity = response.data.search.activity;

  const filteredDays = filterDays(userActivity, dailyData);
  const size = Object.keys(filteredDays).length;
  if (size == 0) {
    $(`#activity${e.target.id}`).append(
      "<div class='text-xl font-bold text-gray-200'>No days fit this activity</div>"
    );
  } else {
    for (day in filteredDays) {
      console.log(dailyData[day]);
      collectHtmlCardData(day, e);
    }
  }
}

function collectHtmlCardData(day, e) {
  const dayData = dailyData[day];
  let icon = dayData.weather[0].icon;
  let theme = "light";
  let showMoon;
  const timeOfDay = Object.keys(filteredDays[day][0]).filter(
    (time) => !["min", "max"].includes(time)
  );

  if (filteredDays[day][1] == false) {
    showMoon = "hidden";
  }
  if (timeOfDay.includes("night")) {
    icon = icon.slice(0, 2) + "n";
    theme = "dark";
  }
  const times = {
    dt: makeDateReadable(dayData.dt),
    sunrise: makeTimeReadable(dayData.sunrise),
    sunset: makeTimeReadable(dayData.sunset),
    moonrise: makeTimeReadable(dayData.moonrise),
    moonset: makeTimeReadable(dayData.moonset),
  };
  console.log(city);
  console.log("this should be working");
  const dataToSend = {
    city: city,
    state: state,
    timeOfDay: timeOfDay,
    dayIndex: day,
    temp: dayData.temp,
    weather: dayData.weather[0],
    rain: dayData.pop * 100,
    moonPhase: dayData.moon_phase * 100,
    showMoon: showMoon,
    uvi: dayData.uvi,
    icon: icon,
    theme: theme,
    times: times,
    activity: userActivity.name,
    activityId: e.target.id,
  };

  makeHtmlTemplate(dataToSend);
}

function makeHtmlTemplate(dataToSend) {
  $(`#activity${dataToSend.activityId}`).append(`<div> <div class="temps${
    dataToSend.dayIndex
  }">best time to go ${dataToSend.activity} would be on ${
    dataToSend.times.dt
  } in the ${dataToSend.timeOfDay}</div>
    <div class=' grid shadow-inner grid-cols-1 sm:grid-cols-2 sm:gap-4 rounded border-solid  p-3 ${
      dataToSend.theme
    }'><img src="https://openweathermap.org/img/wn/${
    dataToSend.icon
  }@2x.png" alt="">
  <div class="mt-3 ">
  <div>${dataToSend.city}, ${dataToSend.state}</div>
    <h3>${dataToSend.times.dt}</h3>
    </div>
    <div>
    <div>${dataToSend.weather.description}</div>
   <div>High: ${dataToSend.temp.max}&#8457 Low: ${
    dataToSend.temp.min
  }&#8457</div>
   <div>Morning: ${dataToSend.temp.morn}&#8457 <br> Day: ${
    dataToSend.temp.day
  }&#8457 <br> Evening: ${dataToSend.temp.eve}&#8457 <br> Night: ${
    dataToSend.temp.night
  }&#8457</div>
  </div>
  <div>
    <div>Sunrise ${dataToSend.times.sunrise}</div>
    <div>Sunset ${dataToSend.times.sunset}</div>
    <div class="${dataToSend.showMoon} ">
    <div>Moonrise ${dataToSend.times.moonrise}</div>
    <div>Moonset ${dataToSend.times.moonset}</div>
    <div>Moon coverage ${dataToSend.moonPhase}%</div>
    </div>
    <div>Percentage of Rain ${dataToSend.rain}%</div>
    <div>UVI ${dataToSend.uvi} (highest between 11am - 2pm)</div>
    </div>
    </div>
    <form action='/make-post' method='post'>
    <input class='hidden' name='day-data' id="day-data" value='${JSON.stringify(
      dataToSend
    )}' type='text'>
    <button id='${
      dataToSend.dayIndex
    }' type='submit' class="border my-2 ml-0 px-3 py-1 bg-gray-500 rounded hover:bg-gray-700" >Make post</button>
    </form>
    </div>
    `);
}

const daysOfWeek = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

function makeDateReadable(time) {
  return `${daysOfWeek[new Date(time * 1000).getDay()]}, ${new Date(
    time * 1000
  ).toLocaleDateString()}`;
}

function makeTimeReadable(time) {
  return new Date(time * 1000).toLocaleTimeString();
}

async function getData() {
  const response = await axios.get(`/api/get-day-data`);
  dailyData = response.data.search.days.daily;
  city = response.data.search.city;
  state = response.data.search.state;
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

// **************************************************
// Filtering functions
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
