package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.renderer.ExampleModel;
import io.zershyan.examplemod.registry.renderer.layer.ExamplePlayerLayer;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.IEventBus;

public class ExampleModEntityLayers {
    public static final ModelLayerLocation EXAMPLE_LAYER =
            new ModelLayerLocation(ExampleMod.id("example_layer"), "main");

    public static void register(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(EXAMPLE_LAYER, () -> ExampleModel.createExampleLayer(new CubeDeformation(0.25F)));
    }

    public static void addLayer(EntityRenderersEvent.AddLayers event) {
        for (String skin : event.getSkins()) {
            PlayerRenderer renderer = event.getSkin(skin);
            if (renderer != null) {
                renderer.addLayer(new ExamplePlayerLayer<>(renderer, event.getEntityModels()));
            }
        }
    }

    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ExampleModEntities.EXAMPLE_PROJECTILE.get(), ThrownItemRenderer::new);
    }

    public static void doRegister(IEventBus modBus) {
        modBus.addListener(ExampleModEntityLayers::registerRenderers);
        modBus.addListener(ExampleModEntityLayers::register);
        modBus.addListener(ExampleModEntityLayers::addLayer);
    }
}
