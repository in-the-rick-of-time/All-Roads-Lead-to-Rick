import {BrowserRouter as Router, Routes, Route, useNavigate} from "react-router-dom";
import './App.css';
import './style.css'
import Disclaimer from './Disclaimer'
import React from 'react';
import { useForm } from "react-hook-form";
import Form from './Form'


export default function App() {

let navigate = useNavigate();
  return (
    <div className="App">
      <header className="App-header">
        <p>
          All Roads Lead To Rick Roll
        </p>
      <div>
        <Form />
      </div>  

      </header>
    </div>
  );

}


