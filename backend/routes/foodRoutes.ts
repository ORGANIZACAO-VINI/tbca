import express from "express";
import { getFoods, getFood, getApi } from "../controllers/foodController";
const router = express.Router();

router.route("/").get(getApi);

router.route("/alimentos").get(getFoods);

router.route("/id/:codigo").get(getFood);

export default router;
