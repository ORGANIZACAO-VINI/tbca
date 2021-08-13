import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Row, Col, Table, Alert } from "react-bootstrap";
import { Link } from "react-router-dom";
import Message from "../components/Message";
import Loader from "../components/Loader";
import PageSelector from "../components/PageSelector";
import SearchBar from "../components/SearchBar";
import { useQuery } from "../hooks/useQuery";

const SearchScreen = () => {
    const query = useQuery();
    // Pega as queries caso tenha
    let pagina = query.get("pagina") || 1;
    let itemsCount = 0;

    const [alert, setAlert] = useState(false);
    const [food, setFood] = useState([]);
    const [searchTerms, setSearchTerms] = useState();
    const [count, setCount] = useState(0);

    const getCount = (items) => {
        setCount(items);
    };

    const getAlert = (bool) => {
        setAlert(bool);
    };

    // Preciso aprender Redux urgentemente,
    // isso aqui NÃO TÁ LEGAL
    const setPagina = (pag) => {
        pagina = pag;
        console.log(pagina);
        setSearchTerms("");
        getFood(pag);
    };

    const getFood = async (pagina) => {
        const { data } = await axios.get(`/api/alimentos?pagina=${pagina}`);
        setFood(data);
    };

    useEffect(() => {
        const getFood = async () => {
            const { data } = await axios.get(`/api/alimentos?pagina=${pagina}`);
            setFood(data);
        };
        getFood();
    }, [pagina]); // talvez coloque o página aqui

    const getSearchTerms = async (terms) => {
        setSearchTerms(terms);
        let pesquisa = terms.split(" ");
        let query = "";
        for (let i = 0; i < pesquisa.length; i++) {
            query += `&q=${pesquisa[i]}`;
        }
        console.log(query);
        if (terms) {
            const { data } = await axios.get(`/api/alimentos/search?${query}`);

            if (data.message) {
                setFood([{}]);
                getAlert(true);
                console.log("kek 404");
            } else {
                await getCount(data[data.length - 1].totalCount);
                console.log(count);
                getAlert(false);
                setFood(data);
            }
        }
    };
    useEffect(() => {
        getSearchTerms("");
    }, []);

    return (
        <>
            <Container>
                <Row>
                    <Col></Col>
                    <Col>
                        <h3>Tabela de Alimentos</h3>
                    </Col>
                    <Col></Col>
                </Row>
                <SearchBar
                    getSearchTerms={getSearchTerms}
                    searchTerms={searchTerms}
                ></SearchBar>
                {alert ? (
                    <Alert key={"aa"} variant={"warning"}>
                        Nenhum alimento foi encontrado!
                    </Alert>
                ) : (
                    <></>
                )}
                <Row>
                    {food.length > 0 ? (
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
                    )}{" "}
                    <Row>
                        {food.length > 1 ? (
                            <PageSelector
                                key={food}
                                pagina={pagina}
                                setPagina={setPagina}
                                count={count}
                            />
                        ) : (
                            <></>
                        )}
                    </Row>
                </Row>
            </Container>
        </>
    );
};

export default SearchScreen;
