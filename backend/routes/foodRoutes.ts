import express from "express";
import {
    getFoods,
    getFood,
    getApi,
    getFoodByNameSearch,
} from "../controllers/foodController";
const router = express.Router();

router.route("/").get(getApi);

router.route("/alimentos").get(getFoods); // /alimentos?pagina=1

router.route("/id/:codigo").get(getFood);

router.route("/alimentos/search").get(getFoodByNameSearch);

export default router;
