import React from "react";
import DeckGL from "@deck.gl/react";
import { QuantizedMeshTerrainLayer } from "./quantized-mesh-layer";
import InfoBox from "./info-box";
import "./App.css";

const INITIAL_VIEW_STATE = {
  latitude: 48.7,
  longitude: -113.81,
  bearing: -3.3,
  pitch: 65,
  zoom: 11.6,
  maxPitch: 89,
};

class App extends React.Component {
  state = {
    viewState: INITIAL_VIEW_STATE,
    zRange: null,
    meshAlgorithm: "pydelatin",
    loadTexture: true,
  };

  // Update zRange of viewport
  onViewportLoad = (data) => {
    if (!data || data.length === 0 || data.every((x) => !x)) {
      return;
    }

    const { zRange } = this.state;
    const ranges = data.filter(Boolean).map((arr) => {
      const bounds = arr[0].header.boundingBox;
      return bounds.map((bound) => bound[2]);
    });
    const minZ = Math.min(...ranges.map((x) => x[0]));
    const maxZ = Math.max(...ranges.map((x) => x[1]));

    if (!zRange || minZ < zRange[0] || maxZ > zRange[1]) {
      this.setState({ zRange: [minZ, maxZ] });
    }
  };

  render() {
    const { viewState, zRange, meshAlgorithm, loadTexture } = this.state;

    const layers = [
      QuantizedMeshTerrainLayer({
        onViewportLoad: this.onViewportLoad,
        zRange,
        meshAlgorithm,
        loadTexture,
      }),
    ];

    return (
      <div>
        <DeckGL
          // Try to hide tile lod cracks
          style={{
            backgroundColor: "rgb(0, 0, 0)",
          }}
          viewState={viewState}
          layers={layers}
          onViewStateChange={({ viewState }) => this.setState({ viewState })}
          controller={{ touchRotate: true }}
          glOptions={{
            // Tell browser to use discrete GPU if available
            powerPreference: "high-performance",
          }}
        >
          <InfoBox
            meshAlgorithm={meshAlgorithm}
            loadTexture={loadTexture}
            onChange={(newState) => this.setState(newState)}
          />
        </DeckGL>
      </div>
    );
  }
}

export default App;

document.body.style.margin = 0;
