import React, {useState} from "react";
import { useController, useForm} from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import Disclaimer from './Disclaimer'

export default function App() {
  const {register, handleSubmit, formState: {errors}}
  = useForm({defaultValues: {
    APIkey: "",
    youtubeURL: ""}
  });
 
console.log(errors);

  return (
    <div className="App">
      <header className="App-header">
        <p>
          All Roads Lead To Rick Roll
        </p>
       
      <form onSubmit={handleSubmit((data)=>{
        console.log(data);
      })}
      >
        <input className="form-attribute" placeholder="API Key" autoComplete="off"
         {...register("APIkey", {required: "This is a required field."})}
        />
        <Disclaimer />
        <p className='error-render'>{errors.APIkey?.message}</p>
 
        <input className="form-attribute" {...register("youtubeURL",{required: "This is a required field."})}
        placeholder="Youtube URL" autoComplete="off" />
        <p className='error-render'>{errors.APIkey?.message}</p>
        <input type = "submit" value="Lets Go!!" />
       
      </form>  
 
      </header>
    </div>
  );
 
}
 
 