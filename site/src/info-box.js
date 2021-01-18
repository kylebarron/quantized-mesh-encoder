import React from "react";
import {
  Accordion,
  Container,
  Checkbox,
  Icon,
  Select,
} from "semantic-ui-react";

const MESH_OPTIONS = [
  { key: "pydelatin", value: "pydelatin", text: "Algorithm: Delatin" },
  { key: "pymartini", value: "pymartini", text: "Algorithm: Martini" },
];

const VIEW_STATE_OPTIONS = [
  {
    key: "glac",
    value: {
      latitude: 48.7,
      longitude: -113.81,
      bearing: -3.3,
      pitch: 65,
      zoom: 11.6,
      maxPitch: 89,
    },
    text: "Glacier National Park",
  },
  {
    key: "grca",
    value: {
      latitude: 36.07091852096502,
      longitude: -112.00934837595949,
      bearing: -35.19642857142857,
      pitch: 60,
      zoom: 13.574472859832357,
      maxPitch: 89,
    },
    text: "Grand Canyon",
  },
  {
    key: "yose",
    value: {
      latitude: 37.74831303498057,
      longitude: -119.54799204629128,
      bearing: 78.74986923166337,
      pitch: 65,
      zoom: 12.1,
      maxPitch: 89,
    },
    text: "Yosemite Valley",
  },
  {
    key: "mtsthelens",
    value: {
      latitude: 46.2099889639587,
      longitude: -122.18025571716424,
      bearing: 156.227493316285,
      pitch: 53,
      zoom: 12.5,
      maxPitch: 89,
    },
    text: "Mt. St. Helens",
  },
  {
    key: "montblanc",
    value: {
      latitude: 45.86306112220158,
      longitude: 6.861778870346716,
      bearing: 31.589576310589322,
      pitch: 62.6,
      zoom: 11.7,
      maxPitch: 89,
    },
    text: "Mont Blanc",
  },
];

export default function InfoBox(props) {
  const { meshAlgorithm, loadTexture, onChange } = props;

  const panels = [
    {
      key: "main-panel",
      title: "Serverless 3D Terrain",
      content: {
        content: (
          <div>
            <p>
              Uses{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/pydelatin"
              >
                <Icon name="github" />
                <code>pydelatin</code>
              </a>{" "}
              or{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/pymartini"
              >
                <Icon name="github" />
                <code>pymartini</code>
              </a>{" "}
              for mesh generation,{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/quantized-mesh-encoder"
              >
                <Icon name="github" />
                <code>quantized-mesh-encoder</code>
              </a>{" "}
              for encoding to{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/CesiumGS/quantized-mesh"
              >
                quantized mesh
              </a>
              ,{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/dem-tiler"
              >
                <Icon name="github" />
                <code>dem-tiler</code>
              </a>{" "}
              for the serverless API, and{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://deck.gl"
              >
                <code>deck.gl</code>
              </a>{" "}
              for rendering.{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/quantized-mesh-encoder/tree/master/site"
              >
                <Icon name="github" />
                Example source.
              </a>
            </p>

            <p>
              If you look closely, you should be able to see small differences
              between the Delatin and Martini meshes. Namely all of Martini's
              triangles are <i>right</i> triangles, while Delatin doesn't have
              that restriction, allowing it to have a more efficient mesh (fewer
              triangles) for a given maximum error.
            </p>

            <Checkbox
              label="Overlay satellite imagery"
              checked={loadTexture}
              onClick={(event, { checked }) =>
                onChange({ loadTexture: checked })
              }
            />
            <br />
            <Select
              placeholder="Fly to:"
              options={VIEW_STATE_OPTIONS}
              // Always shows placeholder
              value={null}
              onChange={(event, { value }) => onChange({ viewState: value })}
            />
            <Select
              placeholder="Select mesh algorithm"
              options={MESH_OPTIONS}
              value={meshAlgorithm}
              onChange={(event, { value }) =>
                onChange({ meshAlgorithm: value })
              }
            />
          </div>
        ),
      },
    },
  ];

  return (
    <Container
      style={{
        position: "absolute",
        width: 400,
        left: 5,
        top: 5,
        padding: 5,
        maxHeight: "50%",
        zIndex: 1,
        pointerEvents: "auto",
        overflowY: "auto",
        overflow: "visible",
      }}
    >
      <Accordion
        defaultActiveIndex={0}
        styled
        panels={panels}
        style={{
          maxWidth: "90%",
        }}
      />
    </Container>
  );
}
