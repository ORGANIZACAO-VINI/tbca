import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Row, Table } from "react-bootstrap";
import Loader from "../components/Loader";
import { useQuery } from "../hooks/useQuery";

const FoodScreen = ({ match }) => {
    const query = useQuery();
    const [food, setFood] = useState([]);

    //food[0] = {};

    useEffect(() => {
        const getFood = async () => {
            const { data } = await axios.get(`/api/id/${match.params.codigo}`);
            setFood(data);
        };
        getFood();
    }, []);

    return (
        <>
            <Container fluid>
                <Row>
                    <h2>
                        <i class="fas fa-utensils"> </i>
                        {food.nome}
                    </h2>
                    <h4>Código: {food.codigo}</h4>
                    <h4>Grupo: {food.grupo}</h4>
                    <p>
                        Valores de nutrientes e de peso são referentes a parte
                        comestível do alimento.
                    </p>
                    {food && food.codigo ? (
                        <Table striped bordered hover responsive>
                            <thead>
                                <tr>
                                    <th>Componente</th>
                                    <th>Unidade</th>
                                    <th>Valor por 100g</th>
                                    <th>Desvio padrão</th>
                                    <th>Valor mínimo</th>
                                    <th>Valor máximo</th>
                                    <th>Número de dados utilizados</th>
                                    <th>Referências</th>
                                    <th>Tipo de dados</th>
                                </tr>
                            </thead>
                            <tbody>
                                {food.componentes.map((componente) => (
                                    <tr>
                                        <td>{componente.componente}</td>
                                        <td>{componente.unidade}</td>
                                        <td>{componente.valorPor100g}</td>
                                        <td>{componente.desvioPadrao}</td>
                                        <td>{componente.valorMinimo}</td>
                                        <td>{componente.valorMaximo}</td>
                                        <td>
                                            {componente.numeroDeDadosUtilizados}
                                        </td>
                                        <td>{componente.referencias}</td>
                                        <td>{componente.tipoDeDados}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    ) : (
                        <Loader />
                    )}
                </Row>
            </Container>
        </>
    );
};

export default FoodScreen;
