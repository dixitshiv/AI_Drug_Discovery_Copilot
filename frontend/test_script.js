const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const dom = new JSDOM(`<!DOCTYPE html><div id="viewer"></div>`);
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;

const $3Dmol = require("3dmol/build/3Dmol.js");
const viewer = $3Dmol.createViewer(document.getElementById("viewer"), { backgroundColor: "black" });
try {
  viewer.addModel("", "pdbqt");
  viewer.setStyle({}, { cartoon: {} });
  viewer.render();
  console.log("Empty data with pdbqt: success");
} catch (e) {
  console.error("Empty data with pdbqt:", e);
}
