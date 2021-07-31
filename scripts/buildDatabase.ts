// Módulo padrão do node para acessar o filesystem do sistema operacional
var fs = require("fs");
var path = require("path");
import glob from "glob"; // Match files using the patterns the shell uses, like stars and stuff.
import Food from "../backend/models/foodModel";
import mongoose from "mongoose";

const connectDB = async () => {
    try {
        const conn = await mongoose.connect("mongodb://127.0.0.1:27017/tbcax", {
            useUnifiedTopology: true,
            useNewUrlParser: true,
            useCreateIndex: true,
        });

        console.log(`MongoDB Connected ${conn.connection.host}`);
    } catch (error) {
        console.error(`Error: ${error}`);
        process.exit(1);
    }
};
connectDB();

let directory = path.resolve("../tbca-scrapper/data");
let files = glob.sync(`${directory}/*.json`, {});
console.log(files[0]);

const addData = async () => {
    for (let i = 0; i < files.length; i++) {
        const index = JSON.parse(fs.readFileSync(`${files[i]}`, "utf8"));
        console.log(index);
        const food = await Food.insertMany(index);
    }
};

const addOne = async () => {
    const index = JSON.parse(fs.readFileSync(`${files[1]}`, "utf8"));
    console.log(index);
    const food = await Food.insertMany(index);
    console.log(food);
};

addData();
