import React, {useState} from 'react'
import './style.css'

export default function Disclaimer(){
    const [selected, setSelected] = useState(null)
    const toggle = (i)=>{
        if (selected===i){
            return setSelected(null)
        }
        setSelected(i)
    }
    return (
        <div className='wrapper'>
            <div className='accordian'> 

            {data.map((item, i)=>(
                <div className='item'>
                    <div className='title' onClick={()=>toggle(i)}>
                        <h2>{item.display}</h2>
                        <span>{selected===i ? '-' :'+'}</span>
                    </div>
                    <div className={selected===i ? 'content show' :'content'}>{item.text}</div>
                </div>    

            ))}
            </div>

        </div>
    )
    
}

const data=[
    {
        display: "Disclaimer",
        text: "We require  "
    }
]