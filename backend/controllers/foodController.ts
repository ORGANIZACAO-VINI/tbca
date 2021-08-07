import { Request, Response, Router } from "express";
import asyncHandler from "express-async-handler";
import Food from "../models/foodModel";

// @desc Recebe os dados de um conjunto de alimentos, de 100 em 100
// @route GET /api/alimentos/
// @access Publico
const getApi = asyncHandler(async (req: Request, res: Response) => {
    res.json("kek");
});

const getFoods = asyncHandler(async (req: Request, res: Response) => {
    let pagina: number = Number(req.query.pagina) || 1;

    // Collation indica que a query atenderá a características específicas de uma linguagem. Nesse caso, a língua portuguesa.
    // Strenght : 2 significa que irá considerar acentos na hora de ordenar o resultado
    const food = await Food.find({})
        .collation({ locale: "pt", strength: 2 })
        .limit(100) // limita o número de objetos retornados na query
        .sort({ nome: 1 }) // ordena por ordem alfabética
        .skip((pagina - 1) * 100); // mágica pros resultados virem paginados
    const skip = food.map((obj: any) => {
        let rObj = {};
        rObj = {
            codigo: obj.codigo,
            nome: obj.nome,
            nomeIngles: obj.nomeIngles,
            nomeCientifico: obj.nomeCientifico,
            grupo: obj.grupo,
            marca: obj.marca,
        };
        return rObj;
    });
    res.json(skip);
});

// @desc Retorna os dados completos de um alimento específico
// @router GET /api/alimento/
// @access Publico
const getFood = asyncHandler(async (req: Request, res: Response) => {
    const food = await Food.findOne(
        { codigo: req.params.codigo },
        { addresses: { $slice: [0, 1] }, _id: false } // ou então tira, pois é irrelevante
    );
    if (!food) {
        res.status(404);
        throw new Error("Alimento não encontrado");
    }
    res.json(food);
});

export { getFood, getFoods, getApi };
