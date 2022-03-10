import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import jsonfile from './data.json';
var jsonF = jsonfile;
async function printYo() {
  console.log("yo");
}

const numDays = 30;

export default function App() {
  const canvasEl = useRef(null);

  //color constants
  const colors = {
    purple: {
      default: "rgba(149, 76, 233, 1)",
      half: "rgba(149, 76, 233, 0.5)",
      quarter: "rgba(149, 76, 233, 0.25)",
      zero: "rgba(149, 76, 233, 0)"
    },
    indigo: {
      default: "rgba(80, 102, 120, 1)",
      quarter: "rgba(80, 102, 120, 0.25)"
    }
  };

  useEffect(() => {
    const ctx = canvasEl.current.getContext("2d");
    // const ctx = document.getElementById("myChart");

    const gradient = ctx.createLinearGradient(0, 16, 0, 600);
    gradient.addColorStop(0, colors.purple.half);
    gradient.addColorStop(0.65, colors.purple.quarter);
    gradient.addColorStop(1, colors.purple.zero);
    console.log(jsonF);
    const weights = jsonF.map(function(e) {
      return e.price;
    });;

    const labels = jsonF.map(function(e) {
      return e.date;
    });

    var w_sliced = weights.slice(0,numDays);
    var l_sliced = labels.slice(0,numDays);
    const data = {
      //labels here
      labels: l_sliced,
      datasets: [
        {
          backgroundColor: gradient,
          label: "Printify Costs",
          //data here
          data: w_sliced,
          fill: true,
          borderWidth: 2,
          borderColor: colors.purple.default,
          lineTension: 0.2,
          pointBackgroundColor: colors.purple.default,
          pointRadius: 3
        }
      ]
    };
    const config = {
      type: "line",
      data: data
    };
    const myLineChart = new Chart(ctx, config);

    return function cleanup() {
      myLineChart.destroy();
    };
  });


  

  return (
    <div className="App">
      <span>Printify Profit</span>
      <canvas id="myChart" ref={canvasEl} height="100" />
      <button onClick={printYo}>Yo</button>

    </div>
  );
}


