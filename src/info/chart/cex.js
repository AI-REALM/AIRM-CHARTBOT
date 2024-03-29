const puppeteer = require("puppeteer");
const fs = require("fs");

const { exec } = require("child_process");
const exchange = process.argv[2]
const crypto = process.argv[3]
const file_path = process.argv[4]
const indicator = process.argv[5]
const user_style = process.argv[6]
const user_interval = process.argv[7]
const page_indcators = {
  'OBV': "On Balance Volume",
  'ADI': "Accumulation/Distribution",
  'ADX': "Average Directional Index",
  'AO': "Aroon",
  'MACD': "MACD",
  'RSI': "Relative Strength Index",
  'SO': "Stochastic",
  'BB': "Bollinger Bands",
  'IC': "Ichimoku Cloud",
  'MA': "MA Cross",
  'MAE': "MA with EMA Cross",
  'SD':  "Standard Deviation",
  'VWAP': "VWAP",
  'VPVR': "Volume Profile Visible Range",
  'VO': "Volume Oscillator"
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}


(async () => {
  let indicato;
  if (indicator==="nu"){
    indicato=[]
  }
  else {
    indicato = indicator.split(",")
  }

  const browserURL = "http://127.0.0.1:9222";

  const browser = await puppeteer.connect({ browserURL });
  const page = await browser.newPage()

  await page.setViewport({ width:1800, height: 1000});
  
  await page.goto(
    `https://www.tradingview.com/chart/?symbol=${exchange}%3A${crypto}&theme=dark&style=${user_style}&interval=${user_interval}`,
    { timeout: 60000 }
  );
  // await sleep(5000);
  // open-indicators-dialog
  
  try{
    try{
      await page.waitForSelector('div[data-dialog-name="gopro"] button[aria-label="Close"]', {timeout:3000});
      await page.$eval('div[data-dialog-name="gopro"] button[aria-label="Close"]', (el) => {el.click()});
    } catch{
  
    }
    await page.waitForSelector('div.dropdown-pbhJWNrt[data-name="removeAllDrawingTools"] div button', {timeout:1000});
    await page.$eval('div.dropdown-pbhJWNrt[data-name="removeAllDrawingTools"] div button', (el) => {el.click()});
  
    await page.waitForSelector('div.accessible-NQERJsv9.item-jFqVJoPk[data-name="remove-studies"]', {timeout:1000});
    await page.$eval('div.accessible-NQERJsv9.item-jFqVJoPk[data-name="remove-studies"]', (el) => {el.click()});
  
    await page.waitForSelector('button[data-name="open-indicators-dialog"]', {timeout:1000});
    await page.$$eval('button[data-name="open-indicators-dialog"]', (el) => {el[0].click()});
    for (let index = 0; index < indicato.length; index++) {
      let element = indicato[index];
      let title = page_indcators[element]
      await page.waitForSelector(`div[data-title="${title}"]`, {timeout:1000});
      await page.$eval(`div[data-title="${title}"]`, el => el.click());
    }
    await page.waitForSelector('div[data-name="indicators-dialog"] button[data-name="close"]', {timeout:1000});
    await page.$eval('div[data-name="indicators-dialog"] button[data-name="close"]', el => el.click());
    
    await sleep(2000)
    const element = await page.$('div.layout__area--center');
    const box = await element.boundingBox();
  
    // Take a screenshot of the specified element
    await page.screenshot({ path: file_path, clip: box });
    await page.waitForSelector('button.button-merBkM5y.apply-common-tooltip.accessible-merBkM5y[aria-label="Take a snapshot"]')
    await page.$eval('button.button-merBkM5y.apply-common-tooltip.accessible-merBkM5y[aria-label="Take a snapshot"]', (el) => {el.click()});
    await page.waitForSelector('div.accessible-NQERJsv9.item-jFqVJoPk.item-o5a0MQMm.withIcon-jFqVJoPk.withIcon-o5a0MQMm[data-name="copy-link-to-the-chart-image"]')
    await page.$eval('div.accessible-NQERJsv9.item-jFqVJoPk.item-o5a0MQMm.withIcon-jFqVJoPk.withIcon-o5a0MQMm[data-name="copy-link-to-the-chart-image"]', (el) => {el.click()});
    // await page.close();
    // await browser.disconnect();
    await frame.waitForSelector('div.container-TCHLKPuQ.container-success-TCHLKPuQ.notice-Q8oybhDM', {timeout:6000});
    // Read the copied string from the clipboard
    const copiedValue = await page.evaluate(() => navigator.clipboard.readText());
    let returnValue = {
      copy_url: copiedValue,
    };
    await page.close();
    await browser.disconnect();
    console.log(JSON.stringify(returnValue));
    await process.exit(0);
  }catch{
    await page.close()
    await page.close()
  }
})();


// document.querySelector('div.button-TPBYkbxL.button-gbkEfGm4.withText-gbkEfGm4.button-uO7HM85b.apply-common-tooltip.isInteractive-uO7HM85b').click()
