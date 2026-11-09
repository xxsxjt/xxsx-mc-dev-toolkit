package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.datagen.lang.ExampleModKeyLang;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ExampleModCreativeTab {
    public static final DeferredRegister<CreativeModeTab> REGISTRY =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ExampleMod.MODID);

    public static final RegistryObject<CreativeModeTab> EXAMPLE_TAB = REGISTRY.register("example_tab", () ->
            CreativeModeTab.builder()
                    .title(ExampleModKeyLang.CreativeTab)
                    .withTabsBefore(CreativeModeTabs.COMBAT)
                    .icon(() -> ExampleModItems.EXAMPLE_ITEM.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(ExampleModItems.EXAMPLE_ITEM.get());
                        output.accept(ExampleModItems.EXAMPLE_CUSTOM_ITEM.get());
                        output.accept(ExampleModItems.EXAMPLE_BLOCK_ITEM.get());
                        output.accept(ExampleModItems.EXAMPLE_CUSTOM_BLOCK_ITEM.get());
                    })
                    .build());

    public static void doRegister(IEventBus modBus) {
        REGISTRY.register(modBus);
    }
}
