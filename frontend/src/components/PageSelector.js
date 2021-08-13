import React from "react";
import { Pagination, Container, Row, Col } from "react-bootstrap";
import PageItem from "react-bootstrap/PageItem";
import { Link } from "react-router-bootstrap";
const PageSelector = (props) => {
    //let count = props.itemsCount;
    let active = parseInt(props.pagina);
    let items = [];

    console.log("Mult: " + props.count / 100);
    for (let number = 1; number <= 10; number++) {
        items.push(
            <PageItem
                key={number}
                active={number == active}
                onClick={() => {
                    props.setPagina(number);
                }}
            >
                {number}
            </PageItem>
        );
        console.log("eba" + props.count);
    }

    const howManyPages = (count) => {
        let pages = count / 100;
    };

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
                <Pagination.First
                    onClick={() => {
                        props.setPagina(1);
                    }}
                />
                <Pagination.Prev />
                {items}
                <Pagination.Next />
                <Pagination.Last />
            </Pagination>
        </Container>
    );
};

export default PageSelector;
