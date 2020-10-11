import { TileLayer } from "@deck.gl/geo-layers";
import { SimpleMeshLayer } from "@deck.gl/mesh-layers";
import { COORDINATE_SYSTEM } from "@deck.gl/core";
import { load } from "@loaders.gl/core";
import { ImageLoader } from "@loaders.gl/images";
import { QuantizedMeshLoader } from "@loaders.gl/terrain";
import { Matrix4 } from "math.gl";

const DUMMY_DATA = [1];

// With create react app, env variables need to be prefixed with REACT_APP
const MapboxAccessToken = process.env.REACT_APP_MAPBOX_ACCESS_TOKEN;

// Error suggestion from here
// https://www.linkedin.com/pulse/fast-cesium-terrain-rendering-new-quantized-mesh-output-alvaro-huarte/
function getMeshMaxError(z) {
  return (77067.34 / (1 << z)).toFixed(2);
}

function quantizedMeshUrl(opts) {
  const {
    x,
    y,
    z,
    mosaicUrl = "terrarium",
    meshAlgorithm = "pydelatin",
    meshMaxError = 10,
  } = opts;
  const params = {
    url: mosaicUrl,
    mesh_max_error: meshMaxError,
    mesh_algorithm: meshAlgorithm,
    // True for pydelatin, false for pymartini. Not sure why...
    flip_y: meshAlgorithm === "pydelatin",
  };
  const searchParams = new URLSearchParams(params);
  let baseUrl = `https://us-east-1-lambda.kylebarron.dev/dem/mesh/${z}/${x}/${y}.terrain?`;
  return baseUrl + searchParams.toString();
}

export function QuantizedMeshTerrainLayer(opts) {
  const {
    minZoom = 0,
    maxZoom = 15,
    onViewportLoad,
    zRange,
    meshAlgorithm,
    loadTexture,
  } = opts || {};
  return new TileLayer({
    id: "quantized-mesh-tile",
    minZoom,
    maxZoom,
    getTileData: (args) => getTileData({ ...args, meshAlgorithm, loadTexture }),
    renderSubLayers,
    onViewportLoad,
    zRange,
    refinementStrategy: "no-overlap",
    updateTriggers: {
      getTileData: [meshAlgorithm, loadTexture],
    },
  });
}

async function getTileData({ x, y, z, meshAlgorithm, loadTexture }) {
  const meshMaxError = getMeshMaxError(z);
  const terrainUrl = quantizedMeshUrl({ x, y, z, meshMaxError, meshAlgorithm });
  const terrain = load(terrainUrl, QuantizedMeshLoader);

  const imageUrl = `https://api.mapbox.com/v4/mapbox.satellite/${z}/${x}/${y}.png?access_token=${MapboxAccessToken}`;
  let image;
  if (loadTexture) {
    image = load(imageUrl, ImageLoader);
  }
  return Promise.all([terrain, image]);
}

function renderSubLayers(props) {
  const { data, tile } = props;

  const [mesh, texture] = data || [];

  return [
    new SimpleMeshLayer(props, {
      data: DUMMY_DATA,
      mesh,
      texture,
      getPolygonOffset: null,
      coordinateSystem: COORDINATE_SYSTEM.CARTESIAN,
      modelMatrix: getModelMatrix(tile),
      getPosition: (d) => [0, 0, 0],
      // Color to use if surfaceImage is unavailable
      getColor: [200, 200, 200],
      // wireframe: true,
    }),
  ];
}

// From https://github.com/uber/deck.gl/blob/b1901b11cbdcb82b317e1579ff236d1ca1d03ea7/modules/geo-layers/src/mvt-tile-layer/mvt-tile-layer.js#L41-L52
// Necessary when using COORDINATE_SYSTEM.CARTESIAN with the standard web
// mercator viewport
function getModelMatrix(tile) {
  const WORLD_SIZE = 512;
  const worldScale = Math.pow(2, tile.z);

  const xScale = WORLD_SIZE / worldScale;
  const yScale = -xScale;

  const xOffset = (WORLD_SIZE * tile.x) / worldScale;
  const yOffset = WORLD_SIZE * (1 - tile.y / worldScale);

  return new Matrix4()
    .translate([xOffset, yOffset, 0])
    .scale([xScale, yScale, 1]);
}
