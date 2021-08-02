import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Row, Col, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import Food from "../components/Food";
import Message from "../components/Message";
import Loader from "../components/Loader";
import PageSelector from "../components/PageSelector";

const HomeScreen = () => {
    const [food, setFood] = useState([{}]);

    useEffect(() => {
        const getFood = async () => {
            const { data } = await axios.get("/api/alimentos");
            setFood(data);
        };
        getFood();
    }, []);
    console.log(food[0]);
    return (
        <>
            <Container>
                <h1>Alimentos</h1>
                <Row>
                    {food && food[0].codigo ? (
                        <Table striped bordered hover>
                            <thead>
                                <tr>
                                    <th>Codigo</th>
                                    <th>Nome</th>
                                    <th>Nome (Inglês)</th>
                                    <th>Nome Científico</th>
                                    <th>Grupo</th>
                                    <th>Marca</th>
                                </tr>
                            </thead>
                            <tbody>
                                {food.map((alimento) => (
                                    <tr key={alimento.codigo}>
                                        <td>
                                            <Link to={`/id/${alimento.codigo}`}>
                                                {alimento.codigo}
                                            </Link>
                                        </td>
                                        <td>{alimento.nome}</td>
                                        <td>{alimento.nomeIngles}</td>
                                        <td>{alimento.nomeCientifico}</td>
                                        <td>{alimento.grupo}</td>
                                        <td>{alimento.marca}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    ) : (
                        <Loader />
                    )}
                </Row>
            </Container>
            <PageSelector />
        </>
    );
};

export default HomeScreen;
