import mongoose from "mongoose";
const Schema = mongoose.Schema;

const foodSchema = new Schema(
    {
        codigo: { type: String, required: true },
        nome: { type: String, required: true },
        nomeIngles: { type: String },
        nomeCientifico: { type: String },
        grupo: { type: String, required: true },
        marca: { type: String },
        componentes: [
            {
                _id: { id: false },
                componente: { type: String },
                unidade: { type: String },
                valorPor100g: { type: String },
                desvioPadrao: { type: String },
                valorMinimo: { type: String },
                valorMaximo: { type: String },
                numeroDeDadosUtilizados: { type: String },
                referencias: { type: String },
                tipoDeDados: { type: String },
            },
        ],
    },
    {
        timestamps: true,
    }
);

// Da documentação do Mongoose:
// The first argument is the singular name of the collection your model is for.
// Mongoose automatically looks for the plural, lowercased version of your model name.
const Food = mongoose.model("Alimento", foodSchema);

export default Food;
