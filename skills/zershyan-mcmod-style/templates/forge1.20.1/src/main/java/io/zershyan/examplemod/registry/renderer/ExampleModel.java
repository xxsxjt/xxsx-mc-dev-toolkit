package io.zershyan.examplemod.registry.renderer;

import net.minecraft.client.model.HumanoidArmorModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.world.entity.LivingEntity;

public class ExampleModel<T extends LivingEntity> extends HumanoidArmorModel<T> {
    public ExampleModel(ModelPart part) {
        super(part);
    }

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
