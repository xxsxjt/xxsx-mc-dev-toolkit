package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModCreativeTab {
    public static final DeferredRegister<CreativeModeTab> REGISTRY =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ExampleMod.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> EXAMPLE_TAB = REGISTRY.register("example_tab", () ->
            CreativeModeTab.builder()
                    .title(ExampleModKeyLang.CreativeTab)
                    .withTabsBefore(CreativeModeTabs.COMBAT)
                    .icon(() -> ExampleModItems.EXAMPLE_ITEM.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ExampleModItems.EXAMPLE_ITEM.get());
                        output.accept(ExampleModItems.EXAMPLE_CUSTOM_ITEM.get());
                        output.accept(ExampleModBlocks.EXAMPLE_BLOCK.get());
                    })
                    .build());

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}
