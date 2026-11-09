package io.zershyan.examplemod.registry;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import io.zershyan.examplemod.ExampleMod;
import io.zershyan.examplemod.registry.command.ExampleCommand;
import net.minecraft.commands.CommandSourceStack;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

import static net.minecraft.commands.Commands.literal;

public final class ExampleModCommands {
    private static final org.slf4j.Logger LOGGER = org.slf4j.LoggerFactory.getLogger(ExampleModCommands.class);

    public static void doRegister(IEventBus neoBus) {
        neoBus.addListener(ExampleModCommands::commonCommandRegister);
    }

    public static void commonCommandRegister(RegisterCommandsEvent event) {
        LiteralArgumentBuilder<CommandSourceStack> builder = literal(ExampleMod.MODID);
        ExampleCommand.register(builder);
        event.getDispatcher().register(builder);
        LOGGER.debug("Registered /{} command", ExampleMod.MODID);
    }
}
