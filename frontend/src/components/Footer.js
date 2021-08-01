import React from "react";
import { Container, Row, Col } from "react-bootstrap";
const Footer = () => {
    return (
        <footer>
            <Container>
                <Row>
                    <Col className="text-center py-3">
                        Powered by MongoDB, Express, React and Node
                        <br /> Dados de alimentos por{" "}
                        <a href="http://www.tbca.net.br/">TBCA</a>
                    </Col>
                </Row>
            </Container>
            ;
        </footer>
    );
};

export default Footer;
