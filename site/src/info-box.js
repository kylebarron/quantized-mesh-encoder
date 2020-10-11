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

export default function InfoBox(props) {
  const { meshAlgorithm, loadTexture, onChange } = props;

  const panels = [
    {
      key: "main-panel",
      title: "Serverless 3D Terrain Mesh",
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
              for rendering. You can also easily overlay a texture source, e.g.
              Mapbox Satellite tiles, with deck.gl.{" "}
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://github.com/kylebarron/quantized-mesh-encoder/tree/master/site"
              >
                <Icon name="github" />
                Example source.
              </a>
            </p>

            <Checkbox
              label="Overlay satellite imagery"
              value={loadTexture}
              onClick={(event, { checked }) =>
                onChange({ loadTexture: checked })
              }
            />
            <br />
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
        width: 300,
        maxWidth: "50%",
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
      <Accordion defaultActiveIndex={-1} styled panels={panels} />
    </Container>
  );
}
