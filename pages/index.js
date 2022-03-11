import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import jsonRevenue from './shopifyDates.json';
import jsonCost from './printifyCost.json'
import jsonProfit from './profitDates.json'
import {PythonShell} from 'python-shell';

async function printYo() {
  var PythonShell = require('python-shell');
  PythonShell.run('..\\scripts\\moshiCalc\\main.py', null, function (err) {
    if (err) throw err;
    console.log('finished');
  });
}

const numDays = 30;


async function effect(canv, jsonFile, color, labl) {
  useEffect(() => {
    const ctx = canv.current.getContext("2d");
    // const ctx = document.getElementById("myChart");

    const gradient = ctx.createLinearGradient(0, 16, 0, 600);
    gradient.addColorStop(0, color.half);
    gradient.addColorStop(0.65, color.quarter);
    gradient.addColorStop(1, color.zero);
    console.log(jsonFile);
    const weights = jsonFile.map(function(e) {
      return e.price;
    });;

    const labels = jsonFile.map(function(e) {
      return e.date;
    });

    var w_sliced = weights.slice(0,numDays).reverse();
    var l_sliced = labels.slice(0,numDays).reverse();
    const data = {
      //labels here
      labels: l_sliced,
      datasets: [
        {
          backgroundColor: gradient,
          label: labl,
          //data here
          data: w_sliced,
          fill: true,
          borderWidth: 2,
          borderColor: color.default,
          lineTension: 0.2,
          pointBackgroundColor: color.default,
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
}

export default function App() {
  //color constants
  const colors = {
    purple: {
      default: "rgba(149, 76, 233, 1)",
      half: "rgba(149, 76, 233, 0.5)",
      quarter: "rgba(149, 76, 233, 0.25)",
      zero: "rgba(149, 76, 233, 0)"
    },
    red: {
      default: "rgba(255, 0, 0, 1)",
      half: "rgba(255, 0, 0, 0.5)",
      quarter: "rgba(255, 0, 0, 0.25)",
      zero: "rgba(255, 0, 0, 0)"
    },
    blue: {
      default: "rgba(0, 0, 255, 1)",
      half: "rgba(0, 0, 255, 0.5)",
      quarter: "rgba(0, 0, 255, 0.25)",
      zero: "rgba(0, 0, 255, 0)"
    },
    indigo: {
      default: "rgba(80, 102, 120, 1)",
      quarter: "rgba(80, 102, 120, 0.25)"
    }
  };


  const canvasRevenue = useRef(null);
  const canvasCost = useRef(null);
  const canvasProfit = useRef(null);
  
  effect(canvasRevenue, jsonRevenue, colors.blue, "Shopify Revenue")
  effect(canvasCost, jsonCost, colors.red, "Printify Cost")
  effect(canvasProfit, jsonProfit, colors.purple, "Raw Profit")



  

  return (
    <div className="App">
      <span>MoshiProject</span>
      <canvas id="myChart" ref={canvasRevenue} height="100" />
      <canvas id="myChart" ref={canvasCost} height="100" />
      <canvas id="myChart" ref={canvasProfit} height="100" />
      <button onClick={printYo}>Yo</button>

    </div>
  );
}


