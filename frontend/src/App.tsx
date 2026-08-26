import { useEffect, useState, useRef } from 'react'
import "./App.css"

type BusInfo = {
    stop_code: string,
    stop_name: string,
    date: string
    buses: {
        time_12h: string, 
        predicted_arrival: string,
        ending_destination: string
    }[]
}

async function getData(stopId: string) {
  const response = await fetch(`http://localhost:8000/stops/${stopId}`)
  const data = await response.json()  

  return data 
}

function App() {
  const [stopId, setStopId] = useState("")
  const [busesInfo, setBusesInfo] = useState<BusInfo|null>(null)

  async function handleSearch(stopId: string) {
    const data = await getData(stopId)
    setBusesInfo(data)
    console.log(data.buses)
  }

  return (
    <>
      <div> 
        <input type="text" value={stopId} onChange={(e) => setStopId(e.target.value)} />
        <button type="button" onClick={async () => handleSearch(stopId)}>check bus stop</button>
      </div> 

      {busesInfo !== null && (
          <> 
            <div className="stopInfo">
              <p>Stop Code: {busesInfo.stop_code}</p>
              <p>Stop Name: {busesInfo.stop_name}</p>
              <p>date: {busesInfo.date}</p>
            </div>
              <p>bus(s) info:</p>
              {
                busesInfo.buses.map(bus => (
                  <div className="bus">
                      <p>Time: {bus.time_12h}</p>
                      <p>Predicted Arrival: {bus.predicted_arrival}</p>
                      <p>Ending Destination: {bus.ending_destination}</p>
                  </div>
                ))
              }
          </>
        )
      }
    </>
  )
} export default App
