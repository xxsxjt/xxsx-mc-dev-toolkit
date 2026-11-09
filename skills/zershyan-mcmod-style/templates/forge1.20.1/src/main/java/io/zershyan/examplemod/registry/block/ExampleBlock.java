package io.zershyan.examplemod.registry.block;

import io.zershyan.examplemod.registry.block.entity.ExampleBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class ExampleBlock extends Block implements EntityBlock {
    public ExampleBlock(Properties properties) {
        super(properties);
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new ExampleBlockEntity(pos, state);
    }
}
