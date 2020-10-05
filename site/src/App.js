import React, { useState, useRef } from "react";
import DeckGL from "@deck.gl/react";
import { QuantizedMeshTerrainLayer } from "./quantized-mesh-layer";
import InfoBox from "./info-box";
import "./App.css";
import { DeckAdapter } from "@hubble.gl/core";
import { useNextFrame, BasicControls, ResolutionGuide } from "@hubble.gl/react";
import { sceneBuilder } from "./scene";

const INITIAL_VIEW_STATE = {
  latitude: 36.07091852096502,
  longitude: -112.00934837595949,
  bearing: -35.19642857142857,
  pitch: 60,
  zoom: 13.574472859832357,
  maxPitch: 89,
};

// const INITIAL_VIEW_STATE = {
//   longitude: -122.4,
//   latitude: 37.74,
//   zoom: 11,
//   pitch: 30,
//   bearing: 0,
// };

const adapter = new DeckAdapter(sceneBuilder);

const encoderSettings = {
  framerate: 30,
  webm: {
    quality: 0.8,
  },
  jpeg: {
    quality: 0.8,
  },
  gif: {
    sampleInterval: 1000,
  },
};

// class App extends React.Component {
//   state = {
//     viewState: INITIAL_VIEW_STATE,
//     zRange: null,
//   };

//   // Update zRange of viewport
//   onViewportLoad = (data) => {
//     if (!data || data.length === 0 || data.every((x) => !x)) {
//       return;
//     }

//     const { zRange } = this.state;
//     const ranges = data.map((arr) => {
//       const bounds = arr.header.boundingBox;
//       return bounds.map((bound) => bound[2]);
//     });
//     const minZ = Math.min(...ranges.map((x) => x[0]));
//     const maxZ = Math.max(...ranges.map((x) => x[1]));

//     if (!zRange || minZ < zRange[0] || maxZ > zRange[1]) {
//       this.setState({ zRange: [minZ, maxZ] });
//     }
//   };

//   render() {
//     const { viewState, zRange } = this.state;

//     const layers = [
//       QuantizedMeshTerrainLayer({
//         onViewportLoad: this.onViewportLoad,
//         zRange,
//       }),
//     ];

//     return (
//       <div>
//         <DeckGL
//           viewState={viewState}
//           layers={layers}
//           onViewStateChange={({ viewState }) => this.setState({ viewState })}
//           controller={{ touchRotate: true }}
//         />
//         <InfoBox />
//       </div>
//     );
//   }
// }

// export default App;

// document.body.style.margin = 0;

const layers = [
  QuantizedMeshTerrainLayer({
    onViewportLoad: () => null,
    zRange: null,
  }),
];

export default function App() {
  const deckgl = useRef(null);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const nextFrame = useNextFrame();

  return (
    <div style={{ position: "relative" }}>
      <div style={{ position: "absolute" }}>
        <ResolutionGuide />
      </div>
      <DeckGL
        ref={deckgl}
        initialViewState={INITIAL_VIEW_STATE}
        parameters={{
          depthTest: false,
          clearColor: [0 / 255, 0 / 255, 0 / 255, 1],
          // blend: true,
          // blendEquation: GL.FUNC_ADD,
          // blendFunc: [GL.SRC_ALPHA, GL.ONE_MINUS_SRC_ALPHA]
        }}
        layers={layers}
        {...adapter.getProps(deckgl, setReady, nextFrame)}
      />
      <div style={{ position: "absolute" }}>
        {ready && (
          <BasicControls
            adapter={adapter}
            busy={busy}
            setBusy={setBusy}
            encoderSettings={encoderSettings}
          />
        )}
      </div>
    </div>
  );
}
