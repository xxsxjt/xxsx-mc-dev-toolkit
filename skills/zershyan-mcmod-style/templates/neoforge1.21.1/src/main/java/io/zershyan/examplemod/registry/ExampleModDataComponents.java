package io.zershyan.examplemod.registry;

import com.mojang.serialization.Codec;
import io.zershyan.examplemod.ExampleMod;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.codec.ByteBufCodecs;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public class ExampleModDataComponents {
    public static final DeferredRegister<DataComponentType<?>> REGISTRY =
            DeferredRegister.create(Registries.DATA_COMPONENT_TYPE, ExampleMod.MODID);

    public static final DeferredHolder<DataComponentType<?>, DataComponentType<Integer>> EXAMPLE_VALUE =
            REGISTRY.register("example_value", () -> DataComponentType.<Integer>builder()
                    .persistent(Codec.INT)
                    .networkSynchronized(ByteBufCodecs.VAR_INT)
                    .build());

    public static void doRegister(IEventBus modEventBus) {
        REGISTRY.register(modEventBus);
    }
}
