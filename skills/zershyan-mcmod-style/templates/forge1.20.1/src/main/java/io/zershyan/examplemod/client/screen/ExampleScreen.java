package io.zershyan.examplemod.client.screen;

import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.CommonComponents;

public class ExampleScreen extends Screen {
    public ExampleScreen() {
        super(ExampleModKeyLang.ItemExampleDesc.copy());
    }

    @Override
    protected void init() {
        addRenderableWidget(Button.builder(CommonComponents.GUI_DONE, button -> onClose())
                .bounds(width / 2 - 50, height / 2, 100, 20)
                .build());
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        renderBackground(graphics);
        super.render(graphics, mouseX, mouseY, partialTick);
        graphics.drawCenteredString(font, title, width / 2, height / 2 - 30, 0xFFFFFF);
    }
}
