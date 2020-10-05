import { DeckScene, CameraKeyframes } from "@hubble.gl/core";
import { easing } from "popmotion";

export async function sceneBuilder(animationLoop) {
  const keyframes = {
    camera: new CameraKeyframes({
      timings: [0, 5000],
      keyframes: [
        {
          latitude: 36.1238,
          longitude: -112.1356,
          bearing: -64.2458,
          pitch: 63.3130,
          zoom: 11.51,
        },
        {
          latitude: 36.1238,
          longitude: -112.1356,
          bearing: -275.19642857142857,
          pitch: 63.3130,
          zoom: 11.51,
        },
      ],
      easings: [easing.easeInOut],
    }),
  };
  animationLoop.timeline.attachAnimation(keyframes.camera);

  return new DeckScene({
    animationLoop,
    keyframes,
    lengthMs: 5000,
    width: 640,
    height: 480,
  });
}
