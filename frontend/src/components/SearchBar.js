import { React, useState } from "react";
import { Form, Button } from "react-bootstrap";

const SearchBar = () => {
    const [type, setType] = useState();
    const [search, setSearch] = useState();

    const submitHandler = (e) => {
        e.preventDefault();
        console.log(search + " " + type);
    };

    return (
        <Form onSubmit={submitHandler}>
            <Form.Group className="mb-3" controlId="alimento">
                <Form.Label>Alimento</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="Batata, frango, arroz..."
                    value={search}
                    onChange={(e) => {
                        console.log(e.target.value);
                        setSearch(e.target.value);
                    }}
                />
            </Form.Group>

            <Form.Group classname="mb-3" controlId="selectAlimento">
                <Form.Label>Grupo</Form.Label>
                <Form.Control
                    as="select"
                    value={type}
                    onChange={(e) => {
                        console.log(e.target.value);
                        setType(e.target.value);
                    }}
                >
                    <option key={0}>SELECIONE</option>
                    <option key={1}>ALIMENTOS INDUSTRIALIZADOS</option>
                    <option key={2}>ALIMENTOS PARA FINS ESPECIAIS</option>
                    <option key={3}>BEBIDAS</option>
                    <option key={4}>CARNES E DERIVADOS</option>
                    <option key={5}>CEREAIS E DERIVADOS</option>
                    <option key={6}>FAST FOOD</option>
                    <option key={7}>FRUTAS E DERIVADOS</option>
                    <option key={8}>GORDURAS E AZEITES</option>
                    <option key={9}>LEGUMINOSAS E DERIVADOS</option>
                    <option key={10}>LEITE E DERIVADOS</option>
                    <option key={11}>MISCELÂNEA</option>
                    <option key={12}>OVOS E DERIVADOS</option>
                    <option key={13}>PESCADOS E FRUTOS DO MAR</option>
                    <option key={14}>PRODUTOS AÇUCARADOS</option>
                    <option key={15}>SEMENTES E OLEAGINOSAS</option>
                    <option key={16}>VEGETAIS E DERIVADOS</option>
                </Form.Control>
            </Form.Group>
            <Button
                className="btn btn-primary btn-large centerButton"
                onClick={submitHandler}
            >
                Buscar
            </Button>
        </Form>
    );
};

export default SearchBar;
