import React from "react";
import { BrowserRouter as Router, Route } from "react-router-dom";
import { Container } from "react-bootstrap";
import Header from "./components/Header";
import Footer from "./components/Footer";
import HomeScreen from "./screens/HomeScreen";
import FoodScreen from "./screens/FoodScreen";

function App() {
    return (
        <Router>
            <>
                <Header />
                <main>
                    <Route path="/alimentos" component={HomeScreen} exact />{" "}
                    <Route path="/id/:codigo" component={FoodScreen} />
                </main>

                <Footer />
            </>
        </Router>
    );
}

export default App;
