import React, {memo, useRef, useEffect, useState} from "react";

// import { MapContainer, TileLayer, useMap, Marker, Popup } from 'react-leaflet'

// import "assets/Map.css";
// import L from "leaflet";


// mapboxgl.accessToken = 'pk.eyJ1Ijoic2R3MTIzMTIzIiwiYSI6ImNrZzdmYWhzMTA2b3IyeXBidzNmb21mMnQifQ.XJPr3M491oSl0xyG5qOHEQ';

const Map = () => {

  // const mapContainer = useRef(null);
  // const map = useRef(null);
  // const [lng, setLng] = useState(172);
  // const [lat, setLat] = useState(43);
  // const [zoom, setZoom] = useState(9);

  // var map = L.map('map').setView([51.505, -0.09], 13);

  // useEffect(() => {
  //   if (map.current) return; // initialize map only once
  //   map.current = new mapboxgl.Map({
  //     container: mapContainer.current,
  //     style: 'mapbox://styles/mapbox/streets-v12',
  //     center: [lng, lat],
  //     zoom: zoom
  //   });
  // });
  // L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  //   maxZoom: 19,
  //   attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  // }).addTo(map);


  return (
    <div className="border section map-section">
      <div id="map">
        {/* <MapContainer style={{ height: "100%", width: "100%" }}
                      preferCanvas={true}
                      renderer={L.canvas()}>
          </MapContainer> */}
      </div>

        {/*<TileLayer*/}
        {/*  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'*/}
        {/*  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"*/}
        {/*/>*/}
        {/*<Marker position={[51.505, -0.09]}>*/}
        {/*  <Popup>*/}
        {/*    A pretty CSS3 popup. <br /> Easily customizable.*/}
        {/*  </Popup>*/}
        {/*</Marker>*/}

    </div>
  );
};

export default memo(Map);
