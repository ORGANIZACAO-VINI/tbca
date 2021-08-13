import React from "react";
import { BrowserRouter as Router, Route } from "react-router-dom";
import { Container } from "react-bootstrap";
import Header from "./components/Header";
import Footer from "./components/Footer";
import SearchScreen from "./screens/SearchScreen";
import FoodScreen from "./screens/FoodScreen";
import HomeScreen from "./screens/HomeScreen";

function App() {
    return (
        <Router>
            <>
                <Header />
                <main>
                    <Route path="/" component={HomeScreen} exact />
                    <Route path="/alimentos/" component={SearchScreen} exact />
                    <Route path="/id/:codigo" component={FoodScreen} />
                </main>

                <Footer />
            </>
        </Router>
    );
}

export default App;
