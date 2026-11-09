package io.zershyan.examplemod.registry;

import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.renderer.ExampleModel;
import io.zershyan.examplemod.registry.renderer.layer.ExamplePlayerLayer;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.client.resources.PlayerSkin;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;

public class ExampleModEntityLayers {
    public static final ModelLayerLocation EXAMPLE_LAYER =
            new ModelLayerLocation(ExampleMod.id(ExampleMod.MODID), "example_layer");

    public static void register(EntityRenderersEvent.RegisterLayerDefinitions event) {
        LayerDefinition layerDefinition = ExampleModel.createExampleLayer(new CubeDeformation(0.25f));
        event.registerLayerDefinition(EXAMPLE_LAYER, () -> layerDefinition);
    }

    public static void addLayer(EntityRenderersEvent.AddLayers event) {
        for (PlayerSkin.Model model : event.getSkins()) {
            PlayerRenderer renderer = event.getSkin(model);
            if (renderer == null) continue;
            renderer.addLayer(new ExamplePlayerLayer<>(renderer, event.getEntityModels()));
        }
    }

    public static void doRegister(IEventBus modBus) {
        modBus.addListener(ExampleModEntityLayers::register);
        modBus.addListener(ExampleModEntityLayers::addLayer);
    }
}
