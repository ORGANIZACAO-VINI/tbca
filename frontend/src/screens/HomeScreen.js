import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Row, Col, Table, Alert, Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import Message from "../components/Message";
import Loader from "../components/Loader";
import PageSelector from "../components/PageSelector";
import SearchBar from "../components/SearchBar";
import { useQuery } from "../hooks/useQuery";

const HomeScreen = () => {
    return (
        <>
            <Container>
                <Row>
                    <Col
                        md={{ span: 12, offset: 5 }}
                        xs={{ span: 12, offset: 5 }}
                    >
                        <h1>TBCAX</h1>
                    </Col>
                </Row>
            </Container>
        </>
    );
};

export default HomeScreen;
