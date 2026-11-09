package io.zershyan.examplemod.client.screen;

import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.jetbrains.annotations.NotNull;

/** 客户端界面示例 */
public class ExampleScreen extends Screen {

    public ExampleScreen() {
        super(Component.translatable(ExampleModKeyLang.ItemExampleDesc.getString()));
    }

    @Override
    protected void init() {
        addRenderableWidget(Button.builder(Component.literal("OK"), button -> this.onClose())
                .bounds(this.width / 2 - 50, this.height / 2, 100, 20)
                .build());
    }

    @Override
    public void render(@NotNull GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, this.height / 2 - 30, 0xFFFFFF);
    }
}
