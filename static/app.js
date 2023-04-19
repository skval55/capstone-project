console.log("sip");

async function getDayAndActivity(e) {
  console.log(e.target.id);

  const response = await axios.get(`/api/search-activity/${e.target.id}`);
  console.log(response);
  filterDays(response.data.search.activity, response.data.search.days.daily);
}

$(".search-day").click(getDayAndActivity);

function filterDays(activity, days) {
  filteredActivity = filterActivity(activity);
  console.log(filteredActivity);
  daysObj = {};
  for (day in days) {
    const singleDay = {};
    singleDay["temp"] = days[day].temp;
    singleDay["moonPhase"] = days[day].moon_phase;
    singleDay["weatherCondition"] = days[day].weather[0].main;
    singleDay["uvi"] = days[day].uvi;
    daysObj[day] = singleDay;
  }

  for (day in daysObj) {
    const weather_condition = filteredActivity.weather_condition
      .replace("{", "")
      .replace("}", "")
      .split(",");

    console.log(weather_condition);
    console.log(daysObj[day]);
    console.log(daysObj[day]["weatherCondition"]);
    if (!(daysObj[day]["weatherCondition"] in weather_condition)) {
      console.log("gottem");
      return false;
    }

    if (filteredActivity.max_temp) {
      filterMax(days);
    }
    if (filteredActivity.min_temp) {
      filterMin(days, daysObj, filteredActivity);
    }
  }
  console.log(daysObj);
}

function filterActivity(activity) {
  const asArray = Object.entries(activity);
  const filtered = asArray.filter(([key, value]) => value !== null);
  const filteredObj = Object.fromEntries(filtered);
  return filteredObj;
}

function filterMax(days) {
  const asArray = Object.entries(days[day].temp);
  const filtered = asArray.filter(
    ([key, value]) => value < filteredActivity.max_temp
  );
  const filteredTemps = Object.fromEntries(filtered);
  daysObj[day].push(filteredTemps);
}

function filterMin(days, daysObj, filteredActivity) {
  console.log("hello");
  if (filteredActivity.max_temp) {
    for (day in daysObj) {
      console.log(daysObj[day][0]);
      const asArray = Object.entries(daysObj[day][0]);
      const filtered = asArray.filter(
        ([key, value]) => value > filteredActivity.min_temp
      );
      const filteredTemps = Object.fromEntries(filtered);
      daysObj[day][0] = filteredTemps;
    }
  } else {
    for (day in days) {
      const asArray = Object.entries(days[day].temp);
      const filtered = asArray.filter(
        ([key, value]) => value > filteredActivity.min_temp
      );
      const filteredTemps = Object.fromEntries(filtered);
      daysObj[day].push(filteredTemps);
    }
  }
}
