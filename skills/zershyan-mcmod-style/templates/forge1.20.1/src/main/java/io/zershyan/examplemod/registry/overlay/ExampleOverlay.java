package io.zershyan.examplemod.registry.overlay;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import io.zershyan.examplemod.client.ClientState;
import io.zershyan.examplemod.registry.config.ClientConfig;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/** 左上角示例 HUD 叠层 */
@OnlyIn(Dist.CLIENT)
public class ExampleOverlay implements IGuiOverlay {
    public static final String ID = ExampleMod.MODID + "_example_overlay";

    @Override
    public void render(ForgeGui forgeGui, GuiGraphics graphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.player == null || minecraft.options.hideGui || !ClientConfig.SHOW_OVERLAY.get()) return;
        graphics.drawString(minecraft.font, ExampleModKeyLang.OverlayValue.get(ClientState.getValue()),
                4, 4, 0xFFFFFF);
    }
}
