import type { Sprite } from 'three';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';

export class SceneGTAOPass extends GTAOPass {
  override overrideVisibility(): void {
    super.overrideVisibility();
    // GTAO's normal override drops sprite alpha; the inherited cache restores it afterwards.
    this.scene.traverse((object) => {
      if ((object as Sprite).isSprite) object.visible = false;
    });
  }
}
