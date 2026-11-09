package io.zershyan.examplemod.registry.block.entity;

import io.zershyan.examplemod.registry.ExampleModBlockEntityTypes;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class ExampleBlockEntity extends BlockEntity {

    public ExampleBlockEntity(BlockPos pos, BlockState blockState) {
        super(ExampleModBlockEntityTypes.EXAMPLE_BLOCK_ENTITY.get(), pos, blockState);
    }
}
