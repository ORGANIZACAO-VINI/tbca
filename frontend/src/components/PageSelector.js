import React from "react";
import { Pagination, Container, Row, Col } from "react-bootstrap";
import PageItem from "react-bootstrap/PageItem";
import { Link } from "react-router-bootstrap";
const PageSelector = (props) => {
    let active = props.pagina;
    let items = [];
    for (let number = 1; number <= 10; number++) {
        items.push(
            <PageItem key={number} active={number == active}>
                {number}
            </PageItem>
        );
    }

    return (
        /* <Container responsive>
            <Pagination>
                {items}
                <PageItem>
                    <span>></span>
                </PageItem>
            </Pagination>
        </Container>*/
        <Container responsive>
            <Pagination>
                <Pagination.First />
                <Pagination.Prev />
                {items}
                <Pagination.Next />
                <Pagination.Last />
            </Pagination>
        </Container>
    );
};

export default PageSelector;
