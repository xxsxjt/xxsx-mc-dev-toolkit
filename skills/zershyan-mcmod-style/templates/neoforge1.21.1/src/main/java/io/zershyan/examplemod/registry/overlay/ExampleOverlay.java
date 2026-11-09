package io.zershyan.examplemod.registry.overlay;

import io.zershyan.examplemod.ExampleMod;
import net.minecraft.client.DeltaTracker;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.LayeredDraw;
import net.minecraft.resources.ResourceLocation;

/** 左上角示例 HUD 叠层 */
public class ExampleOverlay implements LayeredDraw.Layer {
    public static final ResourceLocation ID = ExampleMod.id("example_overlay");

    @Override
    public void render(GuiGraphics guiGraphics, DeltaTracker deltaTracker) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null) return;
        guiGraphics.drawString(
                minecraft.font,
                "Example: " + minecraft.player.getName().getString(),
                4, 4, 0xFFFFFF);
    }
}
