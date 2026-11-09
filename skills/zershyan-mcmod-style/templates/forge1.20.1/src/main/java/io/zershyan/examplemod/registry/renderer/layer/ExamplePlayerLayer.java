package io.zershyan.examplemod.registry.renderer.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.ExampleModEntityLayers;
import io.zershyan.examplemod.registry.renderer.ExampleModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;

public class ExamplePlayerLayer<T extends LivingEntity, M extends HumanoidModel<T>> extends RenderLayer<T, M> {
    private static final ResourceLocation TEXTURE = ExampleMod.id("textures/entity/example_layer.png");
    private final ExampleModel<T> model;

    public ExamplePlayerLayer(RenderLayerParent<T, M> renderer, EntityModelSet modelSet) {
        super(renderer);
        model = new ExampleModel<>(modelSet.bakeLayer(ExampleModEntityLayers.EXAMPLE_LAYER));
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffer, int packedLight, T entity,
                       float limbSwing, float limbSwingAmount, float partialTick,
                       float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity.isInvisible()) return;
        getParentModel().copyPropertiesTo(model);
        model.setupAnim(entity, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
        model.renderToBuffer(poseStack, buffer.getBuffer(model.renderType(TEXTURE)),
                packedLight, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
    }
}
