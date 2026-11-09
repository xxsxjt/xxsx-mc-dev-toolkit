package io.zershyan.examplemod.registry.renderer;

import net.minecraft.client.model.HumanoidArmorModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.world.entity.LivingEntity;

/** 附加在玩家模型上的自定义模型 */
public class ExampleModel<T extends LivingEntity> extends HumanoidArmorModel<T> {

    public ExampleModel(ModelPart part) {
        super(part);
    }

    /** 构建本模型的 layer 定义 */
    public static LayerDefinition createExampleLayer(CubeDeformation deformation) {
        MeshDefinition mesh = HumanoidArmorModel.createBodyLayer(deformation);
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("example_part",
                CubeListBuilder.create().texOffs(0, 0)
                        .addBox(-1.0F, -1.0F, -1.0F, 2.0F, 2.0F, 2.0F, deformation),
                PartPose.ZERO);
        return LayerDefinition.create(mesh, 64, 32);
    }
}
