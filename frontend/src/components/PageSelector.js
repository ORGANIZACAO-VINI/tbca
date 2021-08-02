import React from "react";
import { Pagination, Container, Row, Col } from "react-bootstrap";
import PageItem from "react-bootstrap/PageItem";
import { Link } from "react-router-bootstrap";
const PageSelector = () => {
    let active = 1;
    let items = [];

    const kek = (number) => {
        //console.log(key);
        active = number;
        //console.log(active);
    };

    for (let number = 1; number <= 15; number++) {
        items.push(
            <PageItem key={number} active={number === active}>
                {number}
            </PageItem>
        );
    }

    return (
        <Container responsive>
            <Pagination>
                {items}
                <PageItem>
                    <span>></span>
                </PageItem>
            </Pagination>
        </Container>
    );
};

export default PageSelector;
