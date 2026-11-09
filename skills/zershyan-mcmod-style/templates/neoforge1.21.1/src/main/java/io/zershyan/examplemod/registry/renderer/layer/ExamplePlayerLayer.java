package io.zershyan.examplemod.registry.renderer.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import io.zershyan.examplemod.registry.ExampleModEntityLayers;
import io.zershyan.examplemod.registry.renderer.ExampleModel;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import org.jetbrains.annotations.NotNull;

/** 挂在玩家渲染器上的附加层 */
public class ExamplePlayerLayer<T extends LivingEntity, M extends HumanoidModel<T>> extends RenderLayer<T, M> {
    private static final ResourceLocation TEXTURE = ResourceLocation.withDefaultNamespace("textures/misc/white.png");

    private final ExampleModel<T> model;

    public ExamplePlayerLayer(RenderLayerParent<T, M> renderer, EntityModelSet modelSet) {
        super(renderer);
        this.model = new ExampleModel<>(modelSet.bakeLayer(ExampleModEntityLayers.EXAMPLE_LAYER));
    }

    @Override
    public void render(@NotNull PoseStack poseStack, @NotNull MultiBufferSource bufferSource, int packedLight,
                       @NotNull T entity, float limbSwing, float limbSwingAmount, float partialTick,
                       float ageInTicks, float netHeadYaw, float headPitch) {
        if (entity.isInvisible()) return;
        this.model.setupAnim(entity, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
        // 附加层只在客户端渲染；使用白色贴图时可直接复用
        Minecraft.getInstance().getTextureManager().getTexture(TEXTURE);
        this.model.renderToBuffer(poseStack, bufferSource.getBuffer(this.model.renderType(TEXTURE)),
                packedLight, OverlayTexture.NO_OVERLAY, 0xFFFFFFFF);
    }
}
