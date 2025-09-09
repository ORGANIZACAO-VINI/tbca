import express, { Request, Response, NextFunction } from "express";
// import connectDB from "./config/db";
import dotenv from "dotenv";
import foodRoutes from "./routes/foodRoutes";
import { notFound, errorHandler } from "./middlewares/errorMiddleware";

const app = express();
dotenv.config();
// connectDB();  // Comentando a conexão com o MongoDB

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rotas
app.use("/api/", foodRoutes);

app.get("/", (req: Request, res: Response) => {
    res.send("API online!");
});

app.use(errorHandler);
app.use(notFound);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    return console.log(
        `server is listening in ${process.env.NODE_ENV || 'development'} mode on port ${PORT}`
    );
});
