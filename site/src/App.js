import React from "react";
import DeckGL from "@deck.gl/react";
import { QuantizedMeshTerrainLayer } from "./quantized-mesh-layer";
import InfoBox from "./info-box";
import "./App.css";

const INITIAL_VIEW_STATE = {
  latitude: 36.07091852096502,
  longitude: -112.00934837595949,
  bearing: -35.19642857142857,
  pitch: 60,
  zoom: 13.574472859832357,
  maxPitch: 89,
};

class App extends React.Component {
  state = {
    viewState: INITIAL_VIEW_STATE,
    zRange: null,
  };

  // Update zRange of viewport
  onViewportLoad = (data) => {
    if (!data || data.length === 0 || data.every((x) => !x)) {
      return;
    }

    const { zRange } = this.state;
    const ranges = data.map((arr) => {
      const bounds = arr.header.boundingBox;
      return bounds.map((bound) => bound[2]);
    });
    const minZ = Math.min(...ranges.map((x) => x[0]));
    const maxZ = Math.max(...ranges.map((x) => x[1]));

    if (!zRange || minZ < zRange[0] || maxZ > zRange[1]) {
      this.setState({ zRange: [minZ, maxZ] });
    }
  };

  render() {
    const { viewState, zRange } = this.state;

    const layers = [
      QuantizedMeshTerrainLayer({
        onViewportLoad: this.onViewportLoad,
        zRange,
      }),
    ];

    return (
      <div>
        <DeckGL
          viewState={viewState}
          layers={layers}
          onViewStateChange={({ viewState }) => this.setState({ viewState })}
          controller={{ touchRotate: true }}
        />
        <InfoBox />
      </div>
    );
  }
}

export default App;

document.body.style.margin = 0;
