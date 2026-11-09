package io.zershyan.examplemod.registry.item;

import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** 示例自定义物品：覆写提示文本 */
public class ExampleItem extends Item {

    public ExampleItem() {
        super(new Item.Properties());
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltipComponents, TooltipFlag tooltipFlag) {
        tooltipComponents.add(ExampleModKeyLang.ItemExampleDesc);
    }
}
