import express from "express";
import { getFoods, getFood } from "../controllers/foodController";
const router = express.Router();

router.route("/:pagina").get(getFoods);
router.route("/id/:codigo").get(getFood);

export default router;
